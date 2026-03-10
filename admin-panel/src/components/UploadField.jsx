import { useRef } from "react";

import { uploadApi } from "../api/upload.api";

export default function UploadField({ onUploaded, label = "Загрузить фото", compact = false }) {
  const inputRef = useRef(null);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const res = await uploadApi.uploadImage(file);
    await onUploaded(res.data.url);
    e.target.value = "";
  };

  if (compact) {
    return (
      <>
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          onChange={handleUpload}
          style={{ display: "none" }}
        />
        <button type="button" onClick={() => inputRef.current?.click()}>
          {label}
        </button>
      </>
    );
  }

  return (
    <div>
      <input type="file" accept="image/*" onChange={handleUpload} />
    </div>
  );
}
