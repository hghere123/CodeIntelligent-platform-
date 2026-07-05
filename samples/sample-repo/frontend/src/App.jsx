import React, { useEffect, useState } from "react";

export default function App() {
  const [status, setStatus] = useState("loading");

  useEffect(() => {
    fetch("/api/health")
      .then((response) => response.json())
      .then((body) => setStatus(body.status));
  }, []);

  return <main>{status}</main>;
}

