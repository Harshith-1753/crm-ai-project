import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

function App() {
  const [formData, setFormData] = useState({
    doctor: "",
    date: "",
    type: "",
    notes: ""
  });

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [history, setHistory] = useState([]);
  const [search, setSearch] = useState("");
  const [editingId, setEditingId] = useState(null);

  const [dashboard, setDashboard] = useState({
    total: 0,
    by_type: {},
    recent: []
  });

  // =========================
  // DATE CONVERT
  // =========================
  const convertDate = (textDate) => {
    if (!textDate || textDate.includes("-")) return textDate;

    const months = {
      january: "01", february: "02", march: "03", april: "04",
      may: "05", june: "06", july: "07", august: "08",
      september: "09", october: "10", november: "11", december: "12"
    };

    try {
      const parts = textDate.toLowerCase().split(" ");
      const month = months[parts[0]];
      const day = parts[1]?.padStart(2, "0");

      if (!month || !day) return "";
      return `2026-${month}-${day}`;
    } catch {
      return "";
    }
  };

  // =========================
  // FETCH DATA
  // =========================
  const fetchHistory = async () => {
    const res = await axios.get("http://127.0.0.1:8000/history");
    setHistory(res.data);
  };

  const fetchDashboard = async () => {
    const res = await axios.get("http://127.0.0.1:8000/dashboard");
    setDashboard(res.data);
  };

  useEffect(() => {
    fetchHistory();
    fetchDashboard();
  }, []);

  // =========================
  // SAVE / UPDATE
  // =========================
  const handleSubmit = async () => {
    try {
      if (editingId) {
        await axios.put(
          `http://127.0.0.1:8000/update/${editingId}`,
          formData
        );
        alert("Updated");
        setEditingId(null);
      } else {
        await axios.post(
          "http://127.0.0.1:8000/log-interaction",
          formData
        );
        alert("Saved");
      }

      setFormData({
        doctor: "",
        date: "",
        type: "",
        notes: ""
      });

      fetchHistory();
      fetchDashboard();
    } catch {
      alert("Error saving");
    }
  };

  // =========================
  // CHAT
  // =========================
  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = input;
    setInput("");

    setMessages(prev => [
      ...prev,
      { text: userMessage, sender: "user" }
    ]);

    const res = await axios.post("http://127.0.0.1:8000/chat", {
      message: userMessage
    });

    const response = res.data;

    if (response.type === "text") {
      setMessages(prev => [
        ...prev,
        { text: response.data, sender: "ai" }
      ]);
    }

    if (response.type === "form") {
      const parsed = response.data;

      setFormData({
        doctor: parsed.doctor || "",
        date: convertDate(parsed.date),
        type: parsed.type || "",
        notes: parsed.notes || ""
      });

      setMessages(prev => [
        ...prev,
        { text: "Form auto-filled using AI", sender: "ai" }
      ]);
    }
  };

  // =========================
  // EDIT / DELETE
  // =========================
  const handleEdit = (item) => {
    setEditingId(item.id);

    setFormData({
      doctor: item.doctor,
      date: convertDate(item.date),
      type: item.type,
      notes: item.notes
    });
  };

  const handleDelete = async (id) => {
    await axios.delete(`http://127.0.0.1:8000/delete/${id}`);
    fetchHistory();
    fetchDashboard();
  };

  // =========================
  // FILTER
  // =========================
  const filteredHistory = history.filter((item) =>
    (item.doctor + item.type + item.notes)
      .toLowerCase()
      .includes(search.toLowerCase())
  );

  // =========================
  // EXPORT
  // =========================
  const downloadCSV = () => {
    window.open("http://127.0.0.1:8000/export");
  };

  return (
    <div className="container">

      {/* LEFT PANEL */}
      <div className="form-section">


        {/* FORM */}
        <h2>{editingId ? "Edit Interaction" : "Interaction Form"}</h2>

        <input
          placeholder="Doctor"
          value={formData.doctor}
          onChange={(e) =>
            setFormData({ ...formData, doctor: e.target.value })
          }
        />

        <input
          type="date"
          value={formData.date}
          onChange={(e) =>
            setFormData({ ...formData, date: e.target.value })
          }
        />

        <input
          placeholder="Type"
          value={formData.type}
          onChange={(e) =>
            setFormData({ ...formData, type: e.target.value })
          }
        />

        <textarea
          placeholder="Notes"
          value={formData.notes}
          onChange={(e) =>
            setFormData({ ...formData, notes: e.target.value })
          }
        />

        <button onClick={handleSubmit}>
          {editingId ? "Update" : "Save"}
        </button>

        
        {/* DASHBOARD */}
        <div className="dashboard">
          <h3>Dashboard</h3>
          <p><strong>Total:</strong> {dashboard.total}</p>

          <p><strong>By Type:</strong></p>
          {Object.entries(dashboard.by_type).map(([k, v]) => (
            <p key={k}>{k}: {v}</p>
          ))}

          <p><strong>Recent:</strong></p>
          {dashboard.recent.map((r) => (
            <p key={r.id}>{r.doctor} - {r.date}</p>
          ))}
        </div>

        <button onClick={downloadCSV} className="export-btn">
          Export CSV
        </button>

        <input
          placeholder="Search..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        {/* HISTORY */}
        <h3>History</h3>
        <div className="history-box">
          {filteredHistory.map((item) => (
            <div key={item.id} className="history-item">

              <div onClick={() => handleEdit(item)}>
                <strong>{item.doctor}</strong> | {item.date} | {item.type}
                <p>{item.notes}</p>
              </div>

              <div>
                <button onClick={() => handleEdit(item)}>Edit</button>
                <button onClick={() => handleDelete(item.id)}>Delete</button>
              </div>

            </div>
          ))}
        </div>
      </div>

      {/* RIGHT PANEL */}
      <div className="chat-section">

        <h2>AI Chat</h2>

        <div className="chat-box">
          {messages.map((msg, i) => (
            <div key={i} className={`message ${msg.sender}`}>
              {msg.text}
            </div>
          ))}
        </div>

        <div className="chat-input">
          <input
            value={input}
            placeholder="Type message..."
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          />
          <button onClick={sendMessage}>Send</button>
        </div>

      </div>
    </div>
  );
}

export default App;

