# Modified for this distribution.
terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = "~> 1.3"
}

provider "aws" {
  region  = var.region
}

module "vpc" {
  source   = "./modules/vpc"
  vpc_cidr = var.vpc_cidr
}

module "recommendations" {
  source          = "./modules/recommendations"
  region          = var.region
  vpc_id          = module.vpc.vpc_id
  subd_public     = module.vpc.subd_public
}

module "image_search" {
  source          = "./modules/image_search"
  region          = var.region
  vpc_id          = module.vpc.vpc_id
  subd_public     = module.vpc.subd_public
}

module "comments" {
  source          = "./modules/comments"
  region          = var.region
  vpc_id          = module.vpc.vpc_id
  subd_public     = module.vpc.subd_public
}

module "webserver" {
  source                            = "./modules/webserver"
  vpc_id                            = module.vpc.vpc_id
  subnet_group_id                   = module.vpc.subnet_group_id
  subd_public                       = module.vpc.subd_public
  comments_api_endpoint     = module.comments.api_invoke_url
  image_search_api_endpoint         = module.image_search.api_invoke_url
  image_search_bucket_name          = module.image_search.sagemaker_similar_images_bucket_name
  recommendations_api_endpoint       = module.recommendations.api_invoke_url
  recommendations_bucket_name        = module.recommendations.sagemaker_recommendation_bucket_name
}

module "front" {
  source          = "./modules/front"
  vpc_id          = module.vpc.vpc_id
  backend_url     = module.webserver.backend_url
}


resource "null_resource" "sleep_after_modules" {
  provisioner "local-exec" {
    command = "sleep 500"
  }

  depends_on = [
    module.vpc,
    module.recommendations,
    module.image_search,
    module.comments,
    module.webserver,
    module.front
  ]
}


resource "null_resource" "cleanup_sagemaker_resources" {
  provisioner "local-exec" {
    when    = "destroy"
    command = <<EOT
      chmod +x scripts/cleanup_sagemaker.sh
      scripts/cleanup_sagemaker.sh
    EOT
  }

  triggers = {
    always_run = timestamp()
  }
}
