import * as React from "react"
import { cn } from "@/lib/utils"

const Alert = React.forwardRef(({ className, variant = "default", ...props }, ref) => {
	const variants = {
		default: "bg-white text-gray-900 border-gray-200",
		destructive: "border-red-200 bg-red-50 text-red-800",
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
