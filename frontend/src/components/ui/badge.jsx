import * as React from "react"
import { cn } from "@/lib/utils"

const badgeVariants = {
	default: "bg-cyan-600 text-slate-950",
	secondary: "bg-slate-900/70 text-cyan-100 border border-cyan-500/20",
	outline: "border border-cyan-500/30 text-cyan-100",
	success: "bg-emerald-950/40 text-emerald-200 border border-emerald-500/30",
	destructive: "bg-red-950/40 text-red-200 border border-red-500/30",
}

function Badge({ className, variant = "default", ...props }) {
	return (
		<div
			className={cn(
				"inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold",
				badgeVariants[variant] || badgeVariants.default,
				className
			)}
			{...props}
		/>
	)
}

export { Badge }
