import * as React from "react"
import { cn } from "@/lib/utils"

const badgeVariants = {
	default: "bg-purple-600 text-white",
	secondary: "bg-gray-100 text-gray-800",
	outline: "border border-gray-300 text-gray-800",
	success: "bg-green-100 text-green-800",
	destructive: "bg-red-100 text-red-800",
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
