const API_BASE = (location.hostname === "localhost" || location.hostname === "127.0.0.1")
  ? "http://127.0.0.1:8000"
  : ""; // ajuste se publicar a API em outro domínio

document.getElementById('ask').addEventListener('click', async () => {
  const q = document.getElementById('q').value.trim();
  if(!q) return;
  const meta = document.getElementById('meta');
  const ans = document.getElementById('answer');
  meta.textContent = "consultando...";
  ans.textContent = "";

  const res = await fetch(`${API_BASE}/ask`, {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({ query: q })
  });
  const data = await res.json();
  meta.textContent = `hits: locais ${data?.debug?.local_hits ?? 0} • sumários ${data?.debug?.abstract_hits ?? 0}`;
  ans.textContent = data.answer || "(sem resposta)";
});
