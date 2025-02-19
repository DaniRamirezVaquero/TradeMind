export interface FunctionCall {
  name: string;
  arguments: string;
}

export interface Message {
  content: string;
  type: 'AI' | 'Human' | 'tool_result';
  id?: string;
  additional_kwargs?: {
    function_call?: FunctionCall;
  };
}
