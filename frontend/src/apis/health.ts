import axios from "axios";

const serverUrl = import.meta.env.VITE_SERVER_URL;

export async function getHealth() {
    try {
        const response = await axios.get(`${serverUrl}/health`);
        return response.data;
    } catch (error) {
        console.error("Error fetching health:", error);
        throw error;
    }
}
