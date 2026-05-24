async function checkIPO() {
  console.log("checking IPO...");

  const ticker = document.getElementById("ticker").value;
  const shares = document.getElementById("shares").value;
  const status = document.getElementById("status");

  status.innerText = "Checking cloud backend...";

  try {
    const response = await fetch(
      "https://spacex-ipo-watcher.onrender.com/check-ipo",
    );
    const data = await response.json();

    status.innerText = `${data.message} | ${ticker} | shares=${shares} | available=${data.available}`;

    if (data.available === true) {
      alert("IPO available! Go to Schwab now.");
    }
  } catch (error) {
    status.innerText = "Error: backend not responding";
    console.error(error);
  }
}

setInterval(checkIPO, 60000);
