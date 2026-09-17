import { DatasetSearchResult } from '@/core/entities/Chat';

export interface MaterialFile {
    id: string;
    name: string;
}

const FILE_ID_RE = /[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}/;

export function filesFromSources(sources?: DatasetSearchResult[]): MaterialFile[] {
    const seen = new Map<string, MaterialFile>();
    for (const group of sources || []) {
        for (const row of group.results || []) {
            const id = (row.file_id || '').trim();
            const name = (row.file_name || '').trim();
            if (id && name && !seen.has(id)) {
                seen.set(id, { id, name });
            }
        }
    }
    return Array.from(seen.values());
}

export function parseMaterialFileId(href?: string): string | null {
    if (!href) return null;
    const view = href.match(/\/files\/([^/]+)\/view/i);
    if (view) return decodeURIComponent(view[1].trim());
    const material = href.match(/^material:\/\/file\/(.+)$/i);
    if (material) return decodeURIComponent(material[1].trim());
    const bare = href.match(/^material:(.+)$/i);
    if (bare) return decodeURIComponent(bare[1].trim());
    if (FILE_ID_RE.test(href)) {
        const match = href.match(FILE_ID_RE);
        return match ? match[0] : null;
    }
    return null;
}

function escapeRegExp(value: string): string {
    return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/** Wrap known source filenames as markdown links the renderer can open. */
export function linkifyMaterialMentions(content: string, files: MaterialFile[]): string {
    if (!content || files.length === 0) return content;
    const sorted = [...files].sort((a, b) => b.name.length - a.name.length);
    let out = content;
    for (const file of sorted) {
        const href = `/files/${file.id}/view`;
        const md = `[${file.name}](${href})`;
        const escaped = escapeRegExp(file.name);
        out = out.replace(
            new RegExp(`\\[${escaped}\\]\\((?!/files/${escapeRegExp(file.id)}/view)[^)]*\\)`, 'gi'),
            md,
        );
        out = out.replace(new RegExp(`(?<!\\()\\[${escaped}\\](?!\\()`, 'gi'), md);
        out = out.replace(new RegExp(`(?<!\\[)(?<!\\]\\()${escaped}(?!\\))`, 'gi'), md);
    }
    return out;
}
