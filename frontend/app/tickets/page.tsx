import TicketsPanel from "@/components/TicketsPanel";

export default function TicketsPage({
  searchParams,
}: {
  searchParams: { id?: string };
}) {
  return <TicketsPanel initialExpandedId={searchParams.id} />;
}
