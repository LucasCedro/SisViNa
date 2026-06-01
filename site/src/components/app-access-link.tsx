import type { ComponentProps } from "react";
import { getAppLoginUrl } from "@/lib/app-url";

type AppAccessLinkProps = Omit<ComponentProps<"a">, "href">;

/** Link externo para a tela de login do sistema (Vue). */
export function AppAccessLink({ children, target, rel, ...rest }: AppAccessLinkProps) {
  return (
    <a
      href={getAppLoginUrl()}
      target={target ?? undefined}
      rel={rel ?? (target === "_blank" ? "noopener noreferrer" : undefined)}
      {...rest}
    >
      {children}
    </a>
  );
}
