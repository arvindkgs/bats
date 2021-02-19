import React from 'react';
import clsx from 'clsx';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import useBaseUrl from '@docusaurus/useBaseUrl';
import styles from './styles.module.css';

const features = [
  {
    title: <>Automate Resource comparision</>,
    imageUrl: 'img/compare.png',
    description: (
      <>
        Bats was designed to allow you to automate comparision of values in config files like 
        <code>XML</code> <code>PROPERTIES</code> <code>JSON</code> <code>APACHE config</code> <code>SHELL</code>
      </>
    ),
  },
  {
    title: <>Validate success/failure of shell commands</>,
    imageUrl: 'img/terminal.png',
    description: (
      <>
        Bats lets you run shell commands on remote machines via ssh and verify whether ouput matches a given regex
      </>
    ),
  },
  {
    title: <>Extract values</>,
    imageUrl: 'img/extract.png',
    description: (
      <>
        Bats allows you to extract values of certain properties from one resource and compare them to values of different properties in another resource of same or different type
      </>
    ),
  },
  {
    title: <>Dynamically define locations</>,
    imageUrl: 'img/change.png',
    description: (
      <>
        Bats enables to dynamically define the properties and resource location
      </>
    ),
  },
  {
    title: <>Generate simplified or detailed logs</>,
    imageUrl: 'img/logs.png',
    description: (
      <>
        Bats allows to see simple or verbose logs
      </>
    ),
  },
  {
    title: <>Define complex flows</>,
    imageUrl: 'img/cardinality.png',
    description: (
      <>
        Define complex flows with ‘one-to-one’ or ‘one-to-many’ comparisons
      </>
    ),
  }
];

function Feature({imageUrl, title, description}) {
  const imgUrl = useBaseUrl(imageUrl);
  return (
    <div className={clsx('col col--4', styles.feature)}>
      {imgUrl && (
        <div className="text--center">
          <img className={styles.featureImage} src={imgUrl} alt={title} />
        </div>
      )}
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  );
}

function Home() {
  const context = useDocusaurusContext();
  const {siteConfig = {}} = context;
  return (
    <Layout
      title={`Hello from ${siteConfig.title}`}
      description="Description will go into a meta tag in <head />">
      <header className={clsx('hero hero--primary', styles.heroBanner)}>
        <div className="container">
          <h1 className="hero__title">{siteConfig.title}</h1>
          <p className="hero__subtitle">{siteConfig.tagline}</p>
          <div className={styles.buttons}>
            <Link
              className={clsx(
                'button button--outline button--secondary button--lg',
                styles.getStarted,
              )}
              to={useBaseUrl('docs/')}>
              Get Started
            </Link>
          </div>
        </div>
      </header>
      <main>
        {features && features.length > 0 && (
          <section className={styles.features}>
            <div className="container">
              <div className="row">
                {features.map((props, idx) => (
                  <Feature key={idx} {...props} />
                ))}
              </div>
            </div>
          </section>
        )}
      </main>
    </Layout>
  );
}

export default Home;
