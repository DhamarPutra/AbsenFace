import React, { useState } from "react";
import axios from "axios";
import PORT_API from "./api/port";

const AddMahasiswa = () => {
  const [nama, setNama] = useState("");
  const [nim, setNim] = useState("");
  const [peminatan, setPeminatan] = useState("");
  const [image, setImage] = useState(null);

  const handleImageChange = (event) => {
    setImage(event.target.files[0]); // Menyimpan file gambar yang di-upload
  };

  const handleSubmit = async (event) => {
    event.preventDefault(); // Mencegah reload halaman

    const formData = new FormData();
    formData.append("nama", nama);
    formData.append("nim", nim);
    formData.append("peminatan", peminatan);
    formData.append("image", image);

    try {
      const response = await axios.post(PORT_API + "/add_user", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      alert("Mahasiswa berhasil ditambahkan: " + response.data.message);
      // Reset form setelah berhasil
      setNama("");
      setNim("");
      setPeminatan("");
      setImage(null);
    } catch (error) {
      console.error("Error adding mahasiswa:", error);
      alert("Terjadi kesalahan saat menambahkan mahasiswa.");
    }
  };

  return (
    <div className="bg-blue-50 min-h-screen flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-lg w-full max-w-md">
        <h2 className="text-blue-700 text-2xl font-bold text-center mb-6">
          Add New Face
        </h2>
        <form onSubmit={handleSubmit} encType="multipart/form-data">
          <div className="mb-4">
            <label htmlFor="nama" className="block text-gray-700">
              Nama Mahasiswa
            </label>
            <input
              type="text"
              className="border border-gray-300 p-2 w-full rounded"
              id="nama"
              name="nama"
              value={nama} // Menghubungkan dengan state 'nama'
              onChange={(e) => setNama(e.target.value)} // Update state 'nama'
              required
            />
          </div>
          <div className="mb-4">
            <label htmlFor="nim" className="block text-gray-700">
              NIM
            </label>
            <input
              type="text"
              className="border border-gray-300 p-2 w-full rounded"
              id="nim"
              name="nim"
              value={nim} // Menghubungkan dengan state 'nim'
              onChange={(e) => setNim(e.target.value)} // Update state 'nim'
              required
            />
          </div>
          <div className="mb-4">
            <label htmlFor="peminatan" className="block text-gray-700">
              Peminatan
            </label>
            <input
              type="text"
              className="border border-gray-300 p-2 w-full rounded"
              id="peminatan"
              name="peminatan"
              value={peminatan} // Menghubungkan dengan state 'peminatan'
              onChange={(e) => setPeminatan(e.target.value)} // Update state 'peminatan'
              required
            />
          </div>
          <div className="mb-4">
            <label htmlFor="image" className="block text-gray-700">
              Upload Face Image
            </label>
            <input
              type="file"
              className="border border-gray-300 p-2 w-full rounded"
              id="image"
              name="image"
              accept="image/*"
              onChange={handleImageChange} // Menghubungkan dengan state 'image'
              required
            />
          </div>
          <button
            type="submit"
            className="bg-blue-500 text-white p-2 rounded hover:bg-blue-600 w-full"
          >
            Add Face
          </button>
        </form>
      </div>
    </div>
  );
};

export default AddMahasiswa;
