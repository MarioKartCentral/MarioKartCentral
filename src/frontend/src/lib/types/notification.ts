export type Notification = {
  id: number;
  type: number;
  content_id: number;
  content_args: string[];
  link: string;
  created_date: number;
  is_read: boolean;
};
