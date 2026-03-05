export type Dataset = {
  id: string;
  name: string;
  original_filename: string;
  row_count: number | null;
  column_count: number | null;
  file_size_bytes: number | null;
  status: string;
  created_at: string;
};

export type UploadDatasetPayload = {
  name: string;
  file: File;
};
