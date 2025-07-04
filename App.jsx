import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { Download, Globe, FileImage, FileText, Loader2, CheckCircle, AlertCircle } from 'lucide-react'
import './App.css'

function App() {
  const [url, setUrl] = useState('')
  const [format, setFormat] = useState('png')
  const [isLoading, setIsLoading] = useState(false)
  const [status, setStatus] = useState('')
  const [error, setError] = useState('')

  const handleCapture = async () => {
    if (!url.trim()) {
      setError('URL을 입력해주세요.')
      return
    }

    setIsLoading(true)
    setError('')
    setStatus('웹 페이지를 캡처하는 중...')

    try {
      const response = await fetch('/api/capture', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: url.trim(),
          format: format
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || '캡처에 실패했습니다.')
      }

      setStatus('파일을 다운로드하는 중...')
      
      // 파일 다운로드
      const blob = await response.blob()
      const downloadUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = downloadUrl
      
      // 파일명 생성
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5)
      const extension = format === 'pdf' ? 'pdf' : 'png'
      link.download = `webpage_capture_${timestamp}.${extension}`
      
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(downloadUrl)

      setStatus('캡처가 완료되었습니다!')
      setTimeout(() => setStatus(''), 3000)

    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  const handleUrlChange = (e) => {
    setUrl(e.target.value)
    setError('')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-2xl mx-auto pt-8">
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <Globe className="h-12 w-12 text-blue-600 mr-3" />
            <h1 className="text-4xl font-bold text-gray-900">웹 페이지 캡처 도구</h1>
          </div>
          <p className="text-lg text-gray-600">
            웹 페이지 전체를 고품질 이미지 또는 PDF로 캡처하세요
          </p>
        </div>

        <Card className="shadow-xl border-0">
          <CardHeader className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-t-lg">
            <CardTitle className="flex items-center">
              <Download className="h-6 w-6 mr-2" />
              페이지 캡처
            </CardTitle>
            <CardDescription className="text-blue-100">
              URL을 입력하고 원하는 형식을 선택하여 웹 페이지를 캡처하세요
            </CardDescription>
          </CardHeader>
          <CardContent className="p-6 space-y-6">
            <div className="space-y-2">
              <label htmlFor="url" className="text-sm font-medium text-gray-700">
                웹 페이지 URL
              </label>
              <Input
                id="url"
                type="url"
                placeholder="https://example.com"
                value={url}
                onChange={handleUrlChange}
                className="text-lg"
                disabled={isLoading}
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="format" className="text-sm font-medium text-gray-700">
                파일 형식
              </label>
              <Select value={format} onValueChange={setFormat} disabled={isLoading}>
                <SelectTrigger className="text-lg">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="png">
                    <div className="flex items-center">
                      <FileImage className="h-4 w-4 mr-2" />
                      PNG 이미지
                    </div>
                  </SelectItem>
                  <SelectItem value="pdf">
                    <div className="flex items-center">
                      <FileText className="h-4 w-4 mr-2" />
                      PDF 문서
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {status && !error && (
              <Alert>
                <CheckCircle className="h-4 w-4" />
                <AlertDescription>{status}</AlertDescription>
              </Alert>
            )}

            <Button 
              onClick={handleCapture} 
              disabled={isLoading || !url.trim()}
              className="w-full text-lg py-6 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                  캡처 중...
                </>
              ) : (
                <>
                  <Download className="h-5 w-5 mr-2" />
                  페이지 캡처하기
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        <div className="mt-8 text-center">
          <div className="bg-white rounded-lg p-6 shadow-lg">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">주요 기능</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
              <div className="flex items-center">
                <Globe className="h-5 w-5 text-blue-600 mr-2" />
                전체 페이지 캡처
              </div>
              <div className="flex items-center">
                <FileImage className="h-5 w-5 text-green-600 mr-2" />
                고품질 이미지
              </div>
              <div className="flex items-center">
                <FileText className="h-5 w-5 text-red-600 mr-2" />
                PDF 변환 지원
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App

