export type UserRole = "assistant" | "user";

export type Message = {
  user: UserRole;
  content: string;
  isThinking?: boolean;
};
