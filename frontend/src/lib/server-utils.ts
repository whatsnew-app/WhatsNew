import { cookies } from 'next/headers';

export async function getServerAuthToken() {
  const cookieStore = cookies();
  return cookieStore.get('access_token')?.value;
}

export async function isAuthenticated() {
  return !!await getServerAuthToken();
}