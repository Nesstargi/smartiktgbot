import api from "./axios";

export const getBotSettings = async () => {
  const res = await api.get("/admin/bot-settings/");
  return res.data;
};

export const updateBotSettings = async (data) => {
  const res = await api.put("/admin/bot-settings/", data);
  return res.data;
};
