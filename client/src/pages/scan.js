import React, { useEffect, useRef, useState, useCallback } from "react";
import axios from "axios";
import Webcam from "react-webcam";
import PORT_API from "./api/port";

const Scan = () => {
  const webcamRef = useRef(null);
  const [result, setResult] = useState("");

  const captureAndSendImage = useCallback(async () => {
    if (webcamRef.current) {
      // Capture the screenshot from the webcam
      const imageSrc = webcamRef.current.getScreenshot();
      
      // Prepare the form data
      const formData = new FormData();
      formData.append("image_data", imageSrc); // Send captured image as base64

      try {
        // Send the captured image to the backend
        const response = await axios.post(PORT_API + "/recognize", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });

        // Update the result with the response from the backend
        setResult(response.data.message);
        setTimeout(() => {
          setResult(''); // Clear the result after 2 seconds
        }, 2000);
      } catch (error) {
        const errorMessage = error.response
          ? error.response.data.error
          : "An error occurred";
        setResult(errorMessage);
      }
    }
  }, [webcamRef]);

  // Use setInterval to automatically capture and send images every 5 seconds
  useEffect(() => {
    const intervalId = setInterval(() => {
      captureAndSendImage(); // Capture and send image every 5 seconds
    }, 5000);

    return () => clearInterval(intervalId); // Cleanup on component unmount
  }, [captureAndSendImage]);

  return (
    <div className="bg-blue-50 min-h-screen flex flex-col items-center">
      <h2 className="text-blue-700 text-2xl font-bold my-2">Face Absent</h2>
      <div className="text-center">
        <span className="text-2xl font-bold">
          {result ? result : "Scanning..."}
        </span>
      </div>
      <Webcam
        ref={webcamRef}
        audio={false} // Disable audio
        screenshotFormat="image/jpeg" // Capture the screenshot in JPEG format
        className="border border-gray-300 w-full max-w-lg my-2" // Apply styles
      />
    </div>
  );
};

export default Scan;
