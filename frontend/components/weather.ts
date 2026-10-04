export function weatherIcon(type: string, isDaytime: boolean): string {
  const t = type.toUpperCase();
  if (t.includes("THUNDER")) return "ph-cloud-lightning";
  if (t.includes("SNOW") || t.includes("HAIL") || t.includes("SLEET") || t.includes("FLURR"))
    return "ph-cloud-snow";
  if (t.includes("RAIN") || t.includes("SHOWER") || t.includes("DRIZZLE")) return "ph-cloud-rain";
  if (t.includes("FOG") || t.includes("HAZE") || t.includes("MIST")) return "ph-cloud-fog";
  if (t.includes("WIND")) return "ph-wind";
  if (t === "CLOUDY") return "ph-cloud";
  if (t.includes("CLOUD")) return isDaytime ? "ph-cloud-sun" : "ph-cloud-moon";
  return isDaytime ? "ph-sun" : "ph-moon";
}
