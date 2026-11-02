package com.ragplatform.rag_platform.controller;

import com.ragplatform.rag_platform.model.Message;
import com.ragplatform.rag_platform.repository.MessageRepository;

import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;

@RestController
@RequestMapping("/message")
public class MessageController {

    private final MessageRepository messageRepository;

    public MessageController(MessageRepository messageRepository) {
        this.messageRepository = messageRepository;
    }

    @PostMapping("/send")
    public Message sendMessage(@RequestBody Message message) {

        message.setCreatedAt(LocalDateTime.now());

        return messageRepository.save(message);
    }

    @GetMapping("/chat/{chatId}")
    public List<Message> getMessages(@PathVariable String chatId) {

        return messageRepository.findByChatIdOrderByCreatedAtAsc(chatId);
    }
}