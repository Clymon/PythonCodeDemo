const redeemButton = document.querySelector("#redeem");
redeemButton?.addEventListener("click", async () => {
  redeemButton.disabled = true;
  try {
    const response = await fetch("/api/rewards/first-steps/redeem", {
      method: "POST",
      headers: {"Content-Type":"application/json", "X-CSRF-Token":redeemButton.dataset.token},
      body: "{}"
    });
    if (!response.ok) throw Error((await response.json()).error);
    location.reload();
  } catch (error) {
    document.querySelector("#reward-error").textContent = error.message;
    redeemButton.disabled = false;
  }
});
