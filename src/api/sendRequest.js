import "isomorphic-unfetch";
import notify from "../utils/notify";

let { BACKEND_URL } = process.env || {};
PORT = PORT || 9001;
ROOT_URL = BACKEND_URL || `http://0.0.0.0:${PORT}`;

const sendRequest = async (path, options = {}) => {
  const removeContentType =
    options.headers && options.headers["Remove-Content-Type"];
  let headers;
  if (removeContentType) {
    headers = { ...(options.headers || {}) };
    delete options.headers["Remove-Content-Type"];
  } else {
    headers = {
      "Content-Type": "application/json; charset=UTF-8",
      ...(options.headers || {})
    };
  }

  const response = await fetch(`${ROOT_URL}${path}`, {
    method: "POST",
    credentials: "include",
    ...options,
    headers
  });

  console.log(response);
  if (!response.ok) {
    const failedInformation = await response.json();
    console.log(failedInformation);
    notify({ notificationMessage: failedInformation.detail });
    throw new Error(failedInformation.detail);
  }
  const jsonData = await response.json();

  return jsonData;
};

export default sendRequest;
