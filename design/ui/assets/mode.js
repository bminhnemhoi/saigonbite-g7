// UI/UX stages: ?mode=sketch (stage 1), ?mode=wire (stage 2), default = high-fidelity mock-up (stage 3).
(function () {
  var m = new URLSearchParams(location.search).get("mode");
  if (!m) return;
  if (m === "sketch") {
    var l = document.createElement("link");
    l.rel = "stylesheet";
    l.href = "https://cdn.jsdelivr.net/npm/@fontsource/kalam@5.0.8/400.css";
    document.head.appendChild(l);
  }
  document.addEventListener("DOMContentLoaded", function () {
    document.body.classList.add(m);
    if (m === "sketch") {
      var s = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      s.setAttribute("width", "0"); s.setAttribute("height", "0"); s.style.position = "absolute";
      s.innerHTML = '<filter id="rough"><feTurbulence type="fractalNoise" baseFrequency="0.03" numOctaves="2" seed="7"/>' +
        '<feDisplacementMap in="SourceGraphic" scale="2.6"/></filter>';
      document.body.prepend(s);
    }
  });
})();
