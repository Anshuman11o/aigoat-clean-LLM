// Modified for this distribution.
import React, { useState, useEffect } from 'react';
import { Tooltip, List, Button, Avatar, Input, Form, Comment as AntComment, message } from 'antd';
import GeneralComment from "./Comment";
import { ProductComment } from '../../actions';
import {storeApi} from "../../config";

interface CommentsProps {
  productId: number;
}

const Comments: React.FC<CommentsProps> = ({ productId }) => {
  const [comments, setComments] = useState<ProductComment[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [value, setValue] = useState('');
useEffect(() => {
  if (productId) {
                                              
    storeApi.get(`/products/${productId}/comments`)
      .then(response => {
        const fetchedComments = response.data.map((comment: any) => ({
          author: comment.author,
          avatar: comment.avatar,
          content: <p>{comment.content}</p>,
          datetime: (
            <Tooltip title={new Date(comment.datetime).toLocaleString()}>
              <span>{new Date(comment.datetime).toLocaleTimeString()}</span>
            </Tooltip>
          ),
        }));
        setComments(fetchedComments);
      })
      .catch(error => {
        message.error('Failed to load comments');
        console.error('Error fetching comments:', error);
      });
  }
}, [productId]);

  const handleSubmit = () => {
  if (productId && productId.toString()  !== '0') {
    setSubmitting(true);
    storeApi.post(`/products/${productId}/comments`, { author: 'New User', content: value, is_offensive: [], probability: []})
      .then(response => {
        setSubmitting(false);
        setValue('');
        const newComment = {
          author: 'New User',
          avatar: '/avatar.svg',
          content: <p>{value}</p>,
          datetime: (
            <Tooltip title={new Date().toLocaleString()}>
              <span>{new Date().toLocaleTimeString()}</span>
            </Tooltip>
          ),
        };
                     
        setComments([...comments, newComment]);
      })
    .catch(error => {
      setSubmitting(false);
      if (error.response && error.response.data && error.response.data.error === "Comment is not allowed") {
        message.error('Comment is not allowed due to AI check');
      } else {
        message.error('Failed to add comment');
      }
      console.error('Error adding comment:', error);
    });
} else {
  message.error('Invalid product ID');
}
};


  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setValue(e.target.value);
  };

  return (
    <div style={{ width: "50%" }}>
        {comments && comments.length > 0 && (<List
            dataSource={comments}
            renderItem={(item, index) => (
              <li key={index}>
                <GeneralComment comment={item} />
              </li>
            )}
          />)}
      <AntComment
        avatar={<Avatar src="/avatar.svg" alt="Han Solo" />}
        content={
          <>
            <Form.Item>
              <Input.TextArea rows={4} onChange={handleChange} value={value} />
            </Form.Item>
            <Form.Item>
              <Button
                htmlType="submit"
                loading={submitting}
                onClick={handleSubmit}
                type="primary"
              >
                Add Comment
              </Button>
            </Form.Item>
          </>
        }
      />
    </div>
  );
};

export default Comments;
