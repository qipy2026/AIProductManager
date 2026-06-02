import { redirect } from "next/navigation";

export default function TicketDetailRedirect({ params }: { params: { id: string } }) {
  redirect(`/tickets?id=${encodeURIComponent(params.id)}`);
}
