import Groups from "@/components/Groups";
import Sidebar from "@/components/Sidebar";
import { getStartpage } from "@/lib/server";

export const dynamic = "force-dynamic";

export default async function Home() {
  const data = await getStartpage();
  return (
    <div className="shell">
      <Sidebar authenticated={data.authenticated} />
      <main className="main">
        <Groups groups={data.groups} />
      </main>
    </div>
  );
}
