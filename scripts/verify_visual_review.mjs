import { readFileSync, statSync } from "node:fs";

function pngSize(path) {
  const bytes = readFileSync(path);
  const signature = bytes.subarray(0, 8).toString("hex");
  if (signature !== "89504e470d0a1a0a") throw new Error(`${path} is not a PNG`);
  return { width: bytes.readUInt32BE(16), height: bytes.readUInt32BE(20) };
}

const desktopPath = ".impeccable/review/desktop.png";
const mobilePath = ".impeccable/review/mobile.png";
const detectorPath = ".impeccable/review/detector.json";

for (const path of [desktopPath, mobilePath, detectorPath]) {
  if (statSync(path).size < 10) throw new Error(`${path} is empty`);
}

const desktop = pngSize(desktopPath);
const mobile = pngSize(mobilePath);
if (desktop.width !== 1440 || desktop.height < 1000) {
  throw new Error(`desktop capture has unexpected dimensions: ${desktop.width}x${desktop.height}`);
}
if (mobile.width !== 430 || mobile.height < 932) {
  throw new Error(`mobile capture has unexpected dimensions: ${mobile.width}x${mobile.height}`);
}

const findings = JSON.parse(readFileSync(detectorPath, "utf8"));
const high = findings.filter((finding) => ["high", "error"].includes(finding.severity));
if (high.length) throw new Error(`interface detector has ${high.length} high-severity finding(s)`);

console.log("visual review verification passed");
