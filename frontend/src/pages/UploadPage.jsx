import { useState } from "react";
import toast from "react-hot-toast";
import { useNavigate } from "react-router-dom";
import UploadDropzone from "../components/UploadDropzone.jsx";
import { uploadRepository } from "../services/api.js";

export default function UploadPage() {
  const navigate = useNavigate();
  const [progress, setProgress] = useState(0);
  const [uploading, setUploading] = useState(false);

  const handleUpload = async (file, validationError) => {
    if (validationError) {
      toast.error(validationError);
      return;
    }
    setUploading(true);
    setProgress(5);
    try {
      const result = await uploadRepository(file, setProgress);
      toast.success("Analysis complete");
      navigate(`/analysis/${result.analysis_id}`);
    } catch (error) {
      toast.error(error.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <main className="mx-auto max-w-5xl px-4 py-8">
      <UploadDropzone onUpload={handleUpload} progress={progress} isUploading={uploading} />
    </main>
  );
}

