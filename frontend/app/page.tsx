import { redirect } from 'next/navigation';
import Cookies from 'js-cookie';

export default function Home() {
  const token = Cookies.get('access_token');
  
  if (token) {
    redirect('/dashboard');
  } else {
    redirect('/login');
  }
}