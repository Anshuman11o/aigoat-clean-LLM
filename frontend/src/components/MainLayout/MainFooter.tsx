// Modified for this distribution.
import { Layout } from 'antd';
const { Footer } = Layout;

const MainFooter = () => {
  return (
    <Footer style={{ textAlign: 'center', marginTop: 50 }}>
      Store ©{new Date().getFullYear()} Created by {' '}
      <a href="https://orca.security/" target="_blank">
        @Orca Security
      </a>
    </Footer>
  );
};

export default MainFooter;
