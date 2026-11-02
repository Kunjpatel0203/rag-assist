package com.ragplatform.rag_platform.controller;

import com.ragplatform.rag_platform.model.Chat;
import com.ragplatform.rag_platform.repository.ChatRepository;

import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;

@RestController
@RequestMapping("/chat")
public class ChatController {

    private final ChatRepository chatRepository;

    public ChatController(ChatRepository chatRepository) {
        this.chatRepository = chatRepository;
    }

    @PostMapping("/create")
    public Chat createChat(@RequestBody Chat chat, Authentication authentication) {

        String userEmail = authentication.getName();

        chat.setUserId(userEmail);
        chat.setCreatedAt(LocalDateTime.now());

        return chatRepository.save(chat);
    }

    @GetMapping("/workspace/{workspaceId}")
    public List<Chat> getChatsByWorkspace(@PathVariable String workspaceId) {

        return chatRepository.findByWorkspaceId(workspaceId);
    }
}