import * as React from "react"
import { cn } from "@/lib/utils"

const buttonVariants = {
	default: "bg-purple-600 text-white hover:bg-purple-700",
	outline: "border border-gray-300 bg-white text-gray-800 hover:bg-gray-50",
	ghost: "text-gray-700 hover:bg-gray-100",
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
					"inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-purple-500 disabled:pointer-events-none disabled:opacity-50",
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
