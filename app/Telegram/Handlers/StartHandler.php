<?php

namespace App\Telegram\Handlers;

use App\Telegram\ConversationManager;
use App\Telegram\Keyboards;
use Telegram\Bot\Laravel\Facades\Telegram;
use Telegram\Bot\Objects\Update;

class StartHandler
{
    public function __construct(private ConversationManager $conv) {}

    public function handleCommand(Update $update): void
    {
        $msg    = $update->getMessage();
        $userId = $msg->getFrom()->getId();
        $name   = $msg->getFrom()->getFirstName() ?? 'there';

        $this->conv->clearState($userId);

        Telegram::sendMessage([
            'chat_id'      => $msg->getChat()->getId(),
            'text'         => "Hello, {$name}! What would you like to do?",
            'reply_markup' => json_encode(Keyboards::mainMenu($userId)),
        ]);
    }

    public function handleMainMenu(Update $update): void
    {
        $cbq    = $update->getCallbackQuery();
        $userId = $cbq->getFrom()->getId();
        $chatId = $cbq->getMessage()->getChat()->getId();
        $msgId  = $cbq->getMessage()->getMessageId();

        $this->conv->clearState($userId);

        Telegram::answerCallbackQuery(['callback_query_id' => $cbq->getId()]);

        Telegram::editMessageText([
            'chat_id'      => $chatId,
            'message_id'   => $msgId,
            'text'         => 'Main Menu',
            'reply_markup' => json_encode(Keyboards::mainMenu($userId)),
        ]);
    }
}
