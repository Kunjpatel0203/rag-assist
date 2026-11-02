package com.ragplatform.rag_platform.controller;

import com.ragplatform.rag_platform.dto.RagRequest;
import com.ragplatform.rag_platform.dto.RagResponse;
import com.ragplatform.rag_platform.model.Chat;
import com.ragplatform.rag_platform.model.Message;
import com.ragplatform.rag_platform.repository.ChatRepository;
import com.ragplatform.rag_platform.repository.MessageRepository;

import com.ragplatform.rag_platform.service.AiService;

import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.*;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/ai")
public class AiController {

    private final AiService aiService;

    private final RestTemplate restTemplate;
    private final MessageRepository messageRepository;

    private final ChatRepository chatRepository;

    public AiController(
            RestTemplate restTemplate,
            MessageRepository messageRepository,
            AiService aiService,
            ChatRepository chatRepository
    ) {
        this.restTemplate = restTemplate;
        this.messageRepository = messageRepository;
        this.aiService = aiService;
        this.chatRepository = chatRepository;
    }

//    @PostMapping("/ask")
//    public String askAI(@RequestBody Message message) {
//
//        List<Message> history =
//                messageRepository.findByChatIdOrderByCreatedAtAsc(message.getChatId());
//        int start = Math.max(history.size() - 6, 0);
//        history = history.subList(start, history.size());
//
//        StringBuilder chatHistory = new StringBuilder();
//        System.out.println(chatHistory.toString());
//
//
//
//        for (Message msg : history) {
//            chatHistory.append(msg.getRole())
//                    .append(": ")
//                    .append(msg.getContent())
//                    .append("\n");
//        }
//        // 1️⃣ Save user message
//        message.setRole("user");
//        message.setCreatedAt(LocalDateTime.now());
//        messageRepository.save(message);
//
//        // 2️⃣ Prepare RAG request
//        RagRequest ragRequest = new RagRequest();
//        ragRequest.setCompliance_id("c1");
//        ragRequest.setQuestion(message.getContent());
//        ragRequest.setChatHistory(chatHistory.toString());
//
//        // 3️⃣ Call FastAPI
//        String url = "http://localhost:8000/ask";
//
//        HttpHeaders headers = new HttpHeaders();
//        headers.setContentType(MediaType.APPLICATION_JSON);
//
//        HttpEntity<RagRequest> request =
//                new HttpEntity<>(ragRequest, headers);
//
//        // Call FastAPI through service
//        String answer = aiService.askFastAPI(ragRequest);
//
//        // 4️⃣ Save AI response
//        Message aiMessage = new Message();
//        aiMessage.setChatId(message.getChatId());
//        aiMessage.setRole("assistant");
//        aiMessage.setContent(answer);
//        aiMessage.setCreatedAt(LocalDateTime.now());
//
//        messageRepository.save(aiMessage);
//
//        return answer;
//    }


//    @PostMapping("/ask")
//    public Map<String, String> askAI(@RequestBody Message message) {
//
//        List<Message> history =
//                messageRepository.findByChatIdOrderByCreatedAtAsc(message.getChatId());
//
//        int start = Math.max(history.size() - 6, 0);
//        history = history.subList(start, history.size());
//
//        StringBuilder chatHistory = new StringBuilder();
//
//        for (Message msg : history) {
//            chatHistory.append(msg.getRole())
//                    .append(": ")
//                    .append(msg.getContent())
//                    .append("\n");
//        }
//
//        // 1️⃣ Save user message
//        message.setRole("user");
//        message.setCreatedAt(LocalDateTime.now());
//        messageRepository.save(message);
//
//        // 2️⃣ Prepare RAG request
//        RagRequest ragRequest = new RagRequest();
//        ragRequest.setCompliance_id("c1");
//        ragRequest.setQuestion(message.getContent());
//        ragRequest.setChatHistory(chatHistory.toString());
//
//        // 3️⃣ Call FastAPI
//        String answer = aiService.askFastAPI(ragRequest);
//
//        // 4️⃣ Save AI response
//        Message aiMessage = new Message();
//        aiMessage.setChatId(message.getChatId());
//        aiMessage.setRole("assistant");
//        aiMessage.setContent(answer);
//        aiMessage.setCreatedAt(LocalDateTime.now());
//
//        messageRepository.save(aiMessage);
//
//        return Map.of("answer", answer);
//    }


//    @PostMapping("/ask")
//    public Map<String, String> askAI(@RequestBody Message message) {
//
//        // 1️⃣ Validate chatId
//        if (message.getChatId() == null) {
//            throw new RuntimeException("ChatId is required");
//        }
//
//        // 2️⃣ Find chat to get workspaceId
//        Chat chat = chatRepository
//                .findById(message.getChatId())
//                .orElseThrow(() -> new RuntimeException("Chat not found"));
//
//        // 3️⃣ Load chat history
//        List<Message> history =
//                messageRepository.findByChatIdOrderByCreatedAtAsc(message.getChatId());
//
////        int start = Math.max(history.size() - 2, 0);
////        history = history.subList(start, history.size());
//
////        StringBuilder chatHistory = new StringBuilder();
//
////        for (Message msg : history) {
////            chatHistory.append(msg.getRole())
////                    .append(": ")
////                    .append(msg.getContent())
////                    .append("\n");
////        }
//
////        for (Message msg : history) {
////            if ("user".equals(msg.getRole())) {
////                chatHistory.append(msg.getContent()).append("\n");
////            }
////        }
//
//
//        // ✅ Only take last 2 user messages
//        int start = Math.max(history.size() - 4, 0);
//        history = history.subList(start, history.size());
//
//        String lastUserMessage = "";
//        String prevUserMessage = "";
//
//        for (Message msg : history) {
//            if ("user".equals(msg.getRole())) {
//                prevUserMessage = lastUserMessage;
//                lastUserMessage = msg.getContent();
//            }
//        }
//
//        String question = message.getContent().toLowerCase();
//
//        boolean isFollowUp =
//                question.contains("it") ||
//                        question.contains("they") ||
//                        question.contains("that") ||
//                        question.contains("those") ||
//                        question.contains("these") ||
//                        question.contains("which");
//
//        String finalQuestion = message.getContent();
//
//        if (isFollowUp && lastUserMessage != null && !lastUserMessage.isEmpty()) {
//            finalQuestion = "Based on this context: " + lastUserMessage +
//                    ", answer this: " + message.getContent();
//        }
//        // 4️⃣ Save user message
//        message.setRole("user");
//        message.setCreatedAt(LocalDateTime.now());
//        messageRepository.save(message);
//
//        // 5️⃣ Prepare RAG request
//        RagRequest ragRequest = new RagRequest();
//        ragRequest.setWorkspace_id(chat.getWorkspaceId());
////        ragRequest.setQuestion(message.getContent());
////        ragRequest.setChatHistory(chatHistory.toString());
////        ragRequest.setChatHistory("");
//        ragRequest.setQuestion(finalQuestion);
//        ragRequest.setChatHistory(""); // 🔥 VERY IMPORTANT
//
//        // 6️⃣ Call FastAPI
//        String answer = aiService.askFastAPI(ragRequest);
//
//        // 7️⃣ Save AI response
//        Message aiMessage = new Message();
//        aiMessage.setChatId(message.getChatId());
//        aiMessage.setRole("assistant");
//        aiMessage.setContent(answer);
//        aiMessage.setCreatedAt(LocalDateTime.now());
//
//        messageRepository.save(aiMessage);
//
//        // 8️⃣ Return answer
//        return Map.of("answer", answer);
//    }



    @PostMapping("/ask")
    public Map<String, String> askAI(@RequestBody Message message) {

        if (message.getChatId() == null) {
            throw new RuntimeException("ChatId is required");
        }

        Chat chat = chatRepository
                .findById(message.getChatId())
                .orElseThrow(() -> new RuntimeException("Chat not found"));

        List<Message> history =
                messageRepository.findByChatIdOrderByCreatedAtAsc(message.getChatId());

        // ✅ Last 6 messages
        int start = Math.max(history.size() - 6, 0);
        history = history.subList(start, history.size());

        StringBuilder chatHistory = new StringBuilder();

        for (Message msg : history) {
            chatHistory.append(msg.getRole().toLowerCase())
                    .append(": ")
                    .append(msg.getContent())
                    .append("\n");
        }

        // ✅ Save user message
        message.setRole("user");
        message.setCreatedAt(LocalDateTime.now());
        messageRepository.save(message);

        // ✅ Send clean data
        RagRequest ragRequest = new RagRequest();
        ragRequest.setWorkspace_id(chat.getWorkspaceId());
        ragRequest.setQuestion(message.getContent());
        ragRequest.setChatHistory(chatHistory.toString());

        String answer = aiService.askFastAPI(ragRequest);

        // ✅ Save AI response
        Message aiMessage = new Message();
        aiMessage.setChatId(message.getChatId());
        aiMessage.setRole("assistant");
        aiMessage.setContent(answer);
        aiMessage.setCreatedAt(LocalDateTime.now());

        messageRepository.save(aiMessage);

        return Map.of("answer", answer);
    }
}