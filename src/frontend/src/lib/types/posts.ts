import type { PlayerBasic } from './player';

export type PostBasic = {
  id: number;
  title: string;
  is_public: boolean;
  is_global: boolean;
  creation_date: number;
  created_by: PlayerBasic | null;
};

export type Post = PostBasic & {
  content: string;
};

export type PostList = {
  posts: PostBasic[];
  count: number;
  page_count: number;
};
