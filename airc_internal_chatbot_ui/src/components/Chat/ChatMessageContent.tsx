'use client';

import React, { useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import type { Components } from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { message } from 'antd';
import MermaidRenderer from './MermaidRenderer';
import fileService from '@/services/fileService';
import { DatasetSearchResult } from '@/core/entities/Chat';
import { filesFromSources, linkifyMaterialMentions, parseMaterialFileId } from './materialLinks';

interface ChatMessageContentProps {
  content: string;
  isUser?: boolean;
  sources?: DatasetSearchResult[];
}

export default function ChatMessageContent({
  content,
  isUser = false,
  sources,
}: ChatMessageContentProps) {
  const files = useMemo(() => filesFromSources(sources), [sources]);
  const rendered = useMemo(
    () => (isUser ? content : linkifyMaterialMentions(content, files)),
    [content, files, isUser],
  );

  if (isUser) {
    return <p className="m-0 whitespace-pre-wrap">{content}</p>;
  }

  const markdownComponents: Components = {
    p: ({ ...props }) => <p className="mb-2 leading-relaxed" {...props} />,
    ul: ({ ...props }) => <ul className="list-disc list-outside mb-2 pl-5 space-y-1" {...props} />,
    ol: ({ ...props }) => <ol className="list-decimal list-outside mb-2 pl-5 space-y-1" {...props} />,
    li: ({ ...props }) => <li className="mb-1" {...props} />,
    h1: ({ ...props }) => <h1 className="text-xl font-bold mb-2 mt-4 text-gray-900" {...props} />,
    h2: ({ ...props }) => <h2 className="text-lg font-bold mb-2 mt-3 text-gray-800" {...props} />,
    h3: ({ ...props }) => <h3 className="text-base font-bold mb-2 mt-2 text-gray-800" {...props} />,
    strong: ({ ...props }) => <strong className="font-semibold text-gray-900" {...props} />,
    blockquote: ({ ...props }) => (
      <blockquote className="border-l-4 border-gray-300 pl-4 italic mb-2 text-gray-600" {...props} />
    ),
    a: ({ href, children, ...props }) => {
      const fileId = parseMaterialFileId(href);
      const fileName = files.find((file) => file.id === fileId || file.name === fileId)?.name || fileId;
      const isFileLink = Boolean(
        fileId || (href && (href.startsWith('/files/') || href.includes('/view') || href.endsWith('.pdf')))
      );
      const targetId = fileId || (href ? href.replace(/^\/files\//, '').replace(/\/view$/, '') : '');

      const className =
        'text-[#0F4C81] underline underline-offset-2 hover:text-[#0D9488] font-medium break-all cursor-pointer transition-colors';

      if (isFileLink && targetId) {
        return (
          <a
            href={href}
            className={className}
            target="_blank"
            rel="noopener noreferrer"
            title={`Mở tài liệu: ${fileName || targetId}`}
            onClick={async (event) => {
              event.preventDefault();
              try {
                await fileService.openFileInBrowser(targetId, fileName || targetId);
              } catch (err: any) {
                console.error(err);
                if (err?.response?.status === 404) {
                  message.warning('Tài liệu này hiện chưa có sẵn trên hệ thống.');
                } else {
                  message.error('Không mở được tài liệu. Vui lòng kiểm tra quyền truy cập.');
                }
              }
            }}
            {...props}
          >
            {children}
          </a>
        );
      }
      return (
        <a
          href={href}
          className={className}
          target="_blank"
          rel="noopener noreferrer"
          {...props}
        >
          {children}
        </a>
      );
    },
    code: ({ className, children, ...props }) => {
      const match = /language-(\w+)/.exec(className || '');
      const isInline = !className?.includes('language-');

      if (match && match[1] === 'mermaid') {
        return <MermaidRenderer code={String(children).replace(/\n$/, '')} />;
      }

      return isInline ? (
        <code className="bg-gray-100 px-1 py-0.5 rounded text-sm font-mono text-red-600" {...props}>
          {children}
        </code>
      ) : (
        <code className={`block bg-gray-100 p-3 rounded-lg text-sm font-mono overflow-x-auto mb-2 border border-gray-200 ${className || ''}`} {...props}>
          {children}
        </code>
      );
    },
  };

  return (
    <div className="markdown-content text-gray-800">
      <ReactMarkdown
        remarkPlugins={[remarkMath]}
        rehypePlugins={[rehypeKatex]}
        components={markdownComponents}
      >
        {rendered}
      </ReactMarkdown>
    </div>
  );
}
