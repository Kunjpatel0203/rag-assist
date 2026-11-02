export function Button({ children, className = "", variant, ...props }) {
  let base =
    "px-4 py-2 rounded-lg font-medium transition duration-200";

  let styles =
    variant === "outline"
      ? "border border-white/20 text-white hover:bg-white/10"
      : "bg-white text-black hover:bg-gray-200";

  return (
    <button className={`${base} ${styles} ${className}`} {...props}>
      {children}
    </button>
  );
}