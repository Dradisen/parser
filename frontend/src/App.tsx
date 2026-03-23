import { useEffect, useState } from 'react'
import { MagnifyingGlassIcon } from '@radix-ui/react-icons'
import { Box, Button, Flex, Heading, Text, TextField } from '@radix-ui/themes'

type Marketplace = 'ozon' | 'wildberries'

const marketplaceConfig: Record<
  Marketplace,
  {
    label: string
    logoMark: string
    logoColor: string
    background: string
  }
> = {
  ozon: {
    label: 'Ozon',
    logoMark: 'O',
    logoColor: '#005BFF',
    background: 'linear-gradient(180deg, #E9F1FF 0%, #F7FAFF 52%, #FFFFFF 100%)',
  },
  wildberries: {
    label: 'Wildberries',
    logoMark: 'W',
    logoColor: '#9C0F7A',
    background: 'linear-gradient(180deg, #FBE9F5 0%, #FFF4FB 52%, #FFFFFF 100%)',
  },
}

function App() {
  const [query, setQuery] = useState('')
  const [titleSuffix, setTitleSuffix] = useState('Search')
  const [marketplace, setMarketplace] = useState<Marketplace>('ozon')

  useEffect(() => {
    const from = 'Search'
    const to = 'Parser'

    const sleep = (ms: number) =>
      new Promise((resolve) => window.setTimeout(resolve, ms))

    const randomDelay = (min: number, max: number) =>
      Math.floor(Math.random() * (max - min + 1)) + min

    let isCancelled = false

    const animateLoop = async () => {
      while (!isCancelled) {
        const cycleStartedAt = Date.now()

        for (let i = from.length - 1; i >= 0; i -= 1) {
          if (isCancelled) return
          setTitleSuffix(from.slice(0, i))
          await sleep(randomDelay(70, 160))
        }

        await sleep(randomDelay(140, 260))

        for (let i = 1; i <= to.length; i += 1) {
          if (isCancelled) return
          setTitleSuffix(to.slice(0, i))
          await sleep(randomDelay(75, 170))
        }

        const elapsed = Date.now() - cycleStartedAt
        const rest = Math.max(0, 3000 - elapsed)
        await sleep(rest)

        if (!isCancelled) {
          setTitleSuffix(from)
        }
      }
    }

    animateLoop()

    return () => {
      isCancelled = true
    }
  }, [])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
  }

  return (
    <Flex
      style={{
        minHeight: '100vh',
        background: marketplaceConfig[marketplace].background,
        transition: 'background 280ms ease',
        paddingBottom: '40vh',
      }}
      align="center"
      justify="center"
      direction="column"
      gap="5"
    >
      <Heading size="9" align="center" mb="2">
        {`AI ${titleSuffix}`}
      </Heading>
      <Flex align="center" justify="center" gap="3" wrap="wrap" px="4">
        {(Object.keys(marketplaceConfig) as Marketplace[]).map((key) => {
          const config = marketplaceConfig[key]
          const selected = marketplace === key

          return (
            <Button
              key={key}
              type="button"
              size="3"
              variant={selected ? 'solid' : 'soft'}
              onClick={() => setMarketplace(key)}
              style={{
                border: selected ? `2px solid ${config.logoColor}` : '2px solid transparent',
                background: selected ? '#FFFFFF' : 'rgba(255, 255, 255, 0.72)',
                color: '#111111',
              }}
            >
              <Flex align="center" gap="2">
                <Box
                  style={{
                    width: 24,
                    height: 24,
                    borderRadius: 999,
                    background: config.logoColor,
                    color: '#FFFFFF',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontWeight: 700,
                    fontSize: 13,
                    lineHeight: 1,
                  }}
                >
                  {config.logoMark}
                </Box>
                <Text size="3" weight="medium">
                  {config.label}
                </Text>
              </Flex>
            </Button>
          )
        })}
      </Flex>
      <Box width="100%" style={{ maxWidth: 640 }} px="4">
        <form onSubmit={handleSubmit}>
          <TextField.Root
            size="3"
            placeholder="Поиск"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            style={{ fontSize: '1.2rem' }}
          >
            <TextField.Slot>
              <MagnifyingGlassIcon width={22} height={22} />
            </TextField.Slot>
          </TextField.Root>
        </form>
      </Box>
      {query && (
        <Text color="gray" size="2">
          Parsing {marketplaceConfig[marketplace].label} for: <strong>{query}</strong>
        </Text>
      )}
    </Flex>
  )
}

export default App
