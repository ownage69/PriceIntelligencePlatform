import { ArrowLeft, SearchX } from "lucide-react";
import { Link } from "react-router-dom";

import { EmptyState } from "@/components/common/empty-state";
import { buttonVariants } from "@/components/ui/button-variants";

export function NotFoundPage() {
  return <EmptyState action={<Link className={buttonVariants()} to="/"><ArrowLeft className="size-4" />Back to dashboard</Link>} description="The page you requested does not exist." icon={SearchX} title="Page not found" />;
}
