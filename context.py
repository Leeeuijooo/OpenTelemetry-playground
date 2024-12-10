from opentelemetry.propagate import extract, inject

class ServiceA:
    def client_request():
        inject(headers, context=current_context)
        # Service B 를 호출하고 헤더를 전달
        
class ServiceB:
    def handle_request():
        # Service A 의 요청을 수신
        context = extract(header)