import * as React from "react"
import { cn } from "@/lib/utils"

const Alert = React.forwardRef(({ className, variant = "default", ...props }, ref) => {
	const variants = {
		default: "bg-cyan-950/30 text-cyan-100 border-cyan-500/30",
		destructive: "border-red-500/30 bg-red-950/30 text-red-200",
	}

	return (
		<div
			ref={ref}
			role="alert"
			className={cn("relative w-full rounded-lg border p-4", variants[variant] || variants.default, className)}
			{...props}
		/>
	)
})
Alert.displayName = "Alert"

const AlertDescription = React.forwardRef(({ className, ...props }, ref) => (
	<div ref={ref} className={cn("text-sm [&_p]:leading-relaxed", className)} {...props} />
))
AlertDescription.displayName = "AlertDescription"

export { Alert, AlertDescription }
