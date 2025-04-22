const socket = io();

document.getElementById('generateBtn').addEventListener('click', () => {
  // Clear logs
  document.getElementById('logBox').value = '';

  // Start pipeline on the server side
  socket.emit('start_pipeline');

  // Show the loader on the KPI Dashboard
  const loader = document.getElementById('loader');
  if (loader) loader.style.display = 'block';

  // After 15 seconds, hide loader and show the iframe
  setTimeout(() => {
    if (loader) loader.style.display = 'none';
    const iframe = document.getElementById('dashboardIframe');
    if (iframe) iframe.style.display = 'block';
  }, 15000);
});

socket.on('log', (data) => {
  const logBox = document.getElementById('logBox');
  logBox.value += data.message + '\n';
  logBox.scrollTop = logBox.scrollHeight;
});
