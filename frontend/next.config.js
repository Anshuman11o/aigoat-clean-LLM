// Modified for this distribution.
                    
const withLess = require('@zeit/next-less');
const lessToJS = require('less-vars-to-js');
const fs = require('fs');
const path = require('path');
const FilterWarningsPlugin = require('webpack-filter-warnings-plugin');

                                         
const themeVariables = lessToJS(
  fs.readFileSync(
    path.resolve(__dirname, './src/assets/css/antd-custom.less'),
    'utf8'
  )
);

module.exports = withLess({
  trailingSlash: true,
  output: 'export',
  env: {
    FLASK_API_URL: process.env.FLASK_API_URL
  },
  lessLoaderOptions: {
    javascriptEnabled: true,
    modifyVars: themeVariables                                   
  },
  webpack: (config, { isServer }) => {
    config.plugins.push(
      new FilterWarningsPlugin({
                                                                     
        exclude: /Conflicting order/
      })
    );

    if (isServer) {
      const antStyles = /antd\/.*?\/style.*?/;
      const origExternals = [...config.externals];
      config.externals = [
        (context, request, callback) => {
          if (request.match(antStyles)) return callback();
          if (typeof origExternals[0] === 'function') {
            origExternals[0](context, request, callback);
          } else {
            callback();
          }
        },
        ...(typeof origExternals[0] === 'function' ? [] : origExternals)
      ];

      config.module.rules.unshift({
        test: antStyles,
        use: 'null-loader'
      });
    }
    return config;
  }
});

                                      
                     
                                          
                                                                       
                                    
                      
                                             
        
               
                           
                            
                                
        
      
     



                                                         
  
                                  
                                                            
  
                                      
                        
                       
                 
                                                     
         
       
  
                                                         
                                              
                                                     
                                                 
  
                         
                        
       
  
                                       
                         
                                    
                      
                                             
        
               
                           
                            
                                
         
       
      


                    
                                               
  
                              
                         
                               
       
                                  
                                    
                         
               
                                        
            
                                                          
                       
                              
               
             
            
                                   
                       
                             
                                         
                 
               
             
           
          
  
                        
       
      
