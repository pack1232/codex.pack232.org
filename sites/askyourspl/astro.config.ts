import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  site: 'https://askyourspl.com',
  integrations: [
    starlight({
      title: 'Ask Your SPL',
      description: 'A youth leadership guide for Scouts BSA troops',
      social: [
        { icon: 'github', label: 'GitHub', href: 'https://github.com/pack232/codex.pack232.org' },
      ],
      sidebar: [
        { label: 'Home', link: '/' },
        {
          label: 'Youth Roles',
          autogenerate: { directory: 'roles/youth' },
        },
        {
          label: 'Shared Roles',
          autogenerate: { directory: 'roles/shared' },
          collapsed: true,
        },
        {
          label: 'Training',
          autogenerate: { directory: 'training' },
          collapsed: true,
        },
        {
          label: 'Resources',
          items: [
            { label: 'BSA Policies', link: '/roles/_shared/bsa-policies/' },
            { label: 'Training Requirements', link: '/roles/_shared/training-requirements/' },
          ],
        },
        {
          label: 'Adult Leaders',
          items: [
            { label: 'Adult roles on justonehourperweek.com', link: 'https://justonehourperweek.com/roles/', attrs: { target: '_blank' } },
          ],
        },
      ],
      customCss: ['./src/styles/custom.css'],
      components: {
        Head: './src/components/Head.astro',
      },
    }),
  ],
});
