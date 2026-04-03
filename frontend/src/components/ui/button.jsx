import * as React from "react"
import { cn } from "@/lib/utils"

const buttonVariants = {
	default: "bg-cyan-600 text-slate-950 hover:bg-cyan-500",
	outline: "border border-cyan-500/30 bg-cyan-950/20 text-cyan-100 hover:bg-cyan-900/30",
	ghost: "text-cyan-100 hover:bg-cyan-950/30",
	destructive: "bg-red-600 text-white hover:bg-red-700",
}

const buttonSizes = {
	default: "h-10 px-4 py-2",
	sm: "h-9 px-3 text-sm",
	lg: "h-11 px-8",
	icon: "h-10 w-10",
}

const Button = React.forwardRef(
	({ className, variant = "default", size = "default", type = "button", ...props }, ref) => {
		return (
			<button
				ref={ref}
				type={type}
				className={cn(
					"inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400 disabled:pointer-events-none disabled:opacity-50",
					buttonVariants[variant] || buttonVariants.default,
					buttonSizes[size] || buttonSizes.default,
					className
				)}
				{...props}
			/>
		)
	}
)

Button.displayName = "Button"

export { Button }
