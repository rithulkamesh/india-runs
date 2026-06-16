type IconProps = {
  name: string;
  className?: string;
  fill?: boolean;
  size?: number;
};

/** Material Symbols Outlined glyph. `name` is the ligature, e.g. "dashboard". */
export default function Icon({ name, className = '', fill = false, size }: IconProps) {
  return (
    <span
      className={`material-symbols-outlined select-none ${fill ? 'fill' : ''} ${className}`}
      style={size ? { fontSize: size } : undefined}
      aria-hidden="true"
    >
      {name}
    </span>
  );
}
