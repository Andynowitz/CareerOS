import type { ReactNode } from "react";

type DescriptionBlock =
  | { type: "heading" | "paragraph"; text: string }
  | { type: "list"; items: string[] };

function decodeText(value: string): string {
  return value
    .replace(/&nbsp;/gi, " ")
    .replace(/&amp;/gi, "&")
    .replace(/&lt;/gi, "<")
    .replace(/&gt;/gi, ">")
    .replace(/&quot;/gi, '"')
    .replace(/&#39;|&apos;/gi, "'");
}

function normalizeDescription(description: string): string {
  const hasMarkup = /<\/?(?:p|br|div|h[1-6]|ul|ol|li)\b/i.test(
    description,
  );

  if (!hasMarkup) {
    return description.replace(/\r\n?/g, "\n");
  }

  return description
    .replace(/<br\s*\/?>/gi, "\n")
    .replace(/<\/(?:p|div|h[1-6]|li|ul|ol)>/gi, "\n")
    .replace(/<li\b[^>]*>/gi, "- ")
    .replace(/<[^>]+>/g, "")
    .split("\n")
    .map((line) => decodeText(line).trim())
    .join("\n");
}

function isBullet(line: string): boolean {
  return /^(?:[-*•]|\d+[.)])\s+/.test(line);
}

function cleanBullet(line: string): string {
  return line.replace(/^(?:[-*•]|\d+[.)])\s+/, "").trim();
}

function isHeading(line: string): boolean {
  const withoutMarkdown = line.replace(/^#{1,6}\s+/, "");

  if (withoutMarkdown !== line) {
    return true;
  }

  return (
    withoutMarkdown.length > 1 &&
    withoutMarkdown.length < 90 &&
    (withoutMarkdown.endsWith(":") ||
      (withoutMarkdown === withoutMarkdown.toUpperCase() &&
        /[A-Z]/.test(withoutMarkdown)))
  );
}

function parseDescription(description: string): DescriptionBlock[] {
  const lines = normalizeDescription(description)
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
  const blocks: DescriptionBlock[] = [];

  for (const line of lines) {
    if (isBullet(line)) {
      const previous = blocks.at(-1);

      if (previous?.type === "list") {
        previous.items.push(cleanBullet(line));
      } else {
        blocks.push({ type: "list", items: [cleanBullet(line)] });
      }
      continue;
    }

    const text = line.replace(/^#{1,6}\s+/, "");

    if (isHeading(line)) {
      blocks.push({ type: "heading", text });
    } else {
      blocks.push({ type: "paragraph", text });
    }
  }

  return blocks;
}

interface JobDescriptionProps {
  description: string;
  compact?: boolean;
}

export default function JobDescription({
  description,
  compact = false,
}: JobDescriptionProps) {
  const blocks = parseDescription(description);
  const maxCharacters = 420;
  let charactersShown = 0;
  let isTruncated = false;
  const visibleBlocks: DescriptionBlock[] = [];

  for (const block of blocks) {
    if (!compact) {
      visibleBlocks.push(block);
      continue;
    }

    if (charactersShown >= maxCharacters) {
      isTruncated = true;
      break;
    }

    if (block.type !== "list") {
      const remaining = maxCharacters - charactersShown;
      if (block.text.length <= remaining) {
        visibleBlocks.push(block);
        charactersShown += block.text.length;
      } else {
        visibleBlocks.push({
          ...block,
          text: block.text.slice(0, remaining).trimEnd(),
        });
        isTruncated = true;
        break;
      }
      continue;
    }

    const items: string[] = [];
    for (const item of block.items) {
      const remaining = maxCharacters - charactersShown;
      if (item.length <= remaining) {
        items.push(item);
        charactersShown += item.length;
      } else {
        items.push(item.slice(0, remaining).trimEnd());
        isTruncated = true;
        break;
      }
    }

    if (items.length > 0) {
      visibleBlocks.push({ type: "list", items });
    }
    if (isTruncated) {
      break;
    }
  }

  const renderBlock = (
    block: DescriptionBlock,
    index: number,
  ): ReactNode => {
    if (block.type === "heading") {
      return <h3 key={index}>{block.text}</h3>;
    }

    if (block.type === "list") {
      return (
        <ul key={index}>
          {block.items.map((item, itemIndex) => (
            <li key={`${index}-${itemIndex}`}>{item}</li>
          ))}
        </ul>
      );
    }

    return <p key={index}>{block.text}</p>;
  };

  return (
    <div className={`job-description${compact ? " compact" : ""}`}>
      {visibleBlocks.map(renderBlock)}
      {isTruncated ? <span className="description-more">…</span> : null}
    </div>
  );
}
