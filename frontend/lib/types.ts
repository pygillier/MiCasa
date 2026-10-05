export type Status = "up" | "down" | "pending" | "maintenance" | "paused";

export interface StartLink {
  id: number;
  label: string;
  url: string;
  icon: string;
  host: string;
  status?: Status;
  status_url?: string;
}

export interface Group {
  id: number;
  name: string;
  note: string;
  items: StartLink[];
}

export interface Startpage {
  authenticated: boolean;
  groups: Group[];
}

export interface WeatherData {
  city: string;
  temp: number | null;
  feels_like: number | null;
  condition_type: string;
  condition: string;
  high: number | null;
  low: number | null;
  rain_pct: number | null;
  wind_kmh: number | null;
  is_daytime: boolean;
}

export interface Category {
  id: number;
  name: string;
  note: string;
  position: number;
  is_public: boolean;
}

export interface AdminLink {
  id: number;
  category_id: number;
  label: string;
  url: string;
  icon: string;
  host: string;
  position: number;
  is_public: boolean;
  kuma_monitor_id: number | null;
}

export interface Monitor {
  id: number;
  name: string;
}

export interface Settings {
  weather_city: string;
  weather_lat: string;
  weather_lon: string;
  weather_language: string;
  weather_refresh_minutes: string;
  kuma_base_url: string;
  theme: string;
  google_weather_api_key_configured: boolean;
  google_weather_api_key_tail: string;
}

export interface JobRun {
  id: number;
  job_id: string;
  started_at: string;
  finished_at: string;
  status: "ok" | "error";
  message: string;
}
