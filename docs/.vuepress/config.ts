import {defineUserConfig} from "@vuepress/cli"
import {defaultTheme} from '@vuepress/theme-default'
import * as fs from 'fs';

function get_md_files_names_in_path(path: string) {
    const files = fs.readdirSync(path);
    let file_paths = files.filter((file: string) => file.endsWith('.md'));
    // Filter index.md
    file_paths = file_paths.filter((file: string) => file !== 'index.md');
    return file_paths;
}

export default defineUserConfig({
    repo: 'EvoEvolver/MinimalLLM',
    docsDir: 'docs',
    head: [['link', { rel: 'icon', href: '/image/favicon.ico' }]],
    // @ts-ignore
    theme: defaultTheme({
        logo: '/image/logo.png',
        navbar: [
            {
                text: 'Home',
                link: '/',
            },
            {
                text: 'GitHub',
                link: 'https://github.com/EvoEvolver/MinimalLLM',
            }
        ],
        sidebar: {
            "/": [
                {
                text: 'MinimalLLM Docs',
                children: [
                        {
                            text: 'Home',
                            link: '/',
                        },
                        {
                            text: 'Parsing options',
                            link: '/parsing',
                        }
                    ],
                }
            ],
        },
        sidebarDepth: 2,
    })
})