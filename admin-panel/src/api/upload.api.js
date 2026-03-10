import api from "./axios";

export const uploadApi = {
  uploadImage: (file) => {
    const form = new FormData();
    form.append("file", file);
    return api.post("/admin/upload/file", form);
  },
};
